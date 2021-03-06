import os
import inspect

from api_lib import APITest

DefaultSigningOptions = {
    "Keyring": os.path.join(os.path.dirname(inspect.getsourcefile(APITest)), "files") + "/aptly.pub",
    "SecretKeyring": os.path.join(os.path.dirname(inspect.getsourcefile(APITest)), "files") + "/aptly.sec",
}


class PublishAPITestRepo(APITest):
    """
    POST /publish/:prefix (local repos)
    """
    fixtureGpg = True

    def check(self):
        repo_name = self.random_name()
        self.check_equal(self.post("/api/repos", json={"Name": repo_name, "DefaultDistribution": "wheezy"}).status_code, 201)

        d = self.random_name()
        self.check_equal(self.upload("/api/files/" + d,
                         "libboost-program-options-dev_1.49.0.1_i386.deb", "pyspi_0.6.1-1.3.dsc",
                         "pyspi_0.6.1-1.3.diff.gz", "pyspi_0.6.1.orig.tar.gz",
                         "pyspi-0.6.1-1.3.stripped.dsc").status_code, 200)

        self.check_equal(self.post("/api/repos/" + repo_name + "/file/" + d).status_code, 200)

        # publishing under prefix, default distribution
        prefix = self.random_name()
        resp = self.post("/api/publish/" + prefix,
                         json={
                             "SourceKind": "local",
                             "Sources": [{"Name": repo_name}],
                             "Signing": DefaultSigningOptions,
                         })
        self.check_equal(resp.status_code, 201)
        self.check_equal(resp.json(), {
            'Architectures': ['i386', 'source'],
            'Distribution': 'wheezy',
            'Label': '',
            'Origin': '',
            'Prefix': prefix,
            'SourceKind': 'local',
            'Sources': [{'Component': 'main', 'Name': repo_name}],
            'Storage': ''})

        # publishing under root, custom distribution, architectures
        distribution = self.random_name()
        resp = self.post("/api/publish",
                         json={
                             "SourceKind": "local",
                             "Sources": [{"Name": repo_name}],
                             "Signing": DefaultSigningOptions,
                             "Distribution": distribution,
                             "Architectures": ["i386", "amd64"],
                         })
        self.check_equal(resp.status_code, 201)
        self.check_equal(resp.json(), {
            'Architectures': ['amd64', 'i386'],
            'Distribution': distribution,
            'Label': '',
            'Origin': '',
            'Prefix': ".",
            'SourceKind': 'local',
            'Sources': [{'Component': 'main', 'Name': repo_name}],
            'Storage': ''})


class PublishSnapshotAPITest(APITest):
    """
    POST /publish/:prefix (snapshots)
    """

    def check(self):
        repo_name = self.random_name()
        snapshot_name = self.random_name()
        self.check_equal(self.post("/api/repos", json={"Name": repo_name}).status_code, 201)

        resp = self.post("/api/repos/" + repo_name + '/snapshots', json={'Name': snapshot_name})
        self.check_equal(resp.status_code, 400)

        d = self.random_name()
        self.check_equal(self.upload("/api/files/" + d,
                         "libboost-program-options-dev_1.49.0.1_i386.deb").status_code, 200)

        self.check_equal(self.post("/api/repos/" + repo_name + "/file/" + d).status_code, 200)

        self.check_equal(self.post("/api/repos/" + repo_name + '/snapshots', json={'Name': snapshot_name}).status_code, 201)

        prefix = self.random_name()
        resp = self.post("/api/publish/" + prefix,
                         json={
                             "SourceKind": "snapshot",
                             "Sources": [{"Name": snapshot_name}],
                             "Signing": DefaultSigningOptions,
                             "Distribution": "squeeze",
                         })
        self.check_equal(resp.status_code, 201)
        self.check_equal(resp.json(), {
            'Architectures': ['i386'],
            'Distribution': 'squeeze',
            'Label': '',
            'Origin': '',
            'Prefix': prefix,
            'SourceKind': 'snapshot',
            'Sources': [{'Component': 'main', 'Name': snapshot_name}],
            'Storage': ''})
