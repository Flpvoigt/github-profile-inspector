import unittest
from unittest.mock import patch

import github_profile_inspector as inspector


class ProfileInspectorTests(unittest.TestCase):
    @patch("github_profile_inspector.api_get")
    def test_builds_profile_summary(self, api_get):
        api_get.side_effect = [
            {
                "login": "Flpvoigt",
                "name": "Felipe Voigt",
                "bio": "Backend developer",
                "location": "Timbó - SC",
                "html_url": "https://github.com/Flpvoigt",
                "followers": 4,
                "following": 6,
                "public_repos": 9,
            },
            [
                {
                    "name": "api-project",
                    "fork": False,
                    "language": "Python",
                    "stargazers_count": 3,
                    "html_url": "https://github.com/Flpvoigt/api-project",
                },
                {
                    "name": "forked-project",
                    "fork": True,
                    "language": "Java",
                    "stargazers_count": 99,
                    "html_url": "https://github.com/example/forked-project",
                },
            ],
        ]

        result = inspector.inspect_profile("Flpvoigt")

        self.assertEqual(result["login"], "Flpvoigt")
        self.assertEqual(result["own_repositories_analyzed"], 1)
        self.assertEqual(result["total_stars"], 3)
        self.assertEqual(result["languages"], {"Python": 1})

    @patch("github_profile_inspector.api_get")
    def test_encodes_username(self, api_get):
        api_get.side_effect = [
            {
                "login": "name space",
                "name": None,
                "bio": None,
                "location": None,
                "html_url": "https://github.com/name%20space",
                "followers": 0,
                "following": 0,
                "public_repos": 0,
            },
            [],
        ]

        inspector.inspect_profile("name space")

        self.assertEqual(api_get.call_args_list[0].args[0], "/users/name%20space")


if __name__ == "__main__":
    unittest.main()

