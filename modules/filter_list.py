import os

def filter_list(source_list: list[str], target_list: list[str], *, case_sensitive: bool = True) -> list[str]:
    """
        Filter a list of Path objects based on Unix-style wildcard patterns.

        Args:
            source_list (list[Path]):
                A list of Path objects to filter

            target_list (list[str]):
                A list of patterns to match against each file or directory name
                Supports Unix-style wildcards:
                    ˙'*'  -> matches any number of characters
                    '?'  -> matches a single character
                    '[abc]' -> matches any character in the set

        Returns:
            list[Path]:
                A list of Path objects from 'source_list' that match at least one
                pattern in 'target_list'
        """

    filtered = [
        value for value in source_list
        if any(target in value for target in target_list)
    ]
    
    return filtered

base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "local_test")
source_dirs = os.listdir(base_dir)
target_dirs = []

if __name__ == "__main__":
    print(source_dirs)
    test =filter_list(source_dirs,target_dirs)
    print(test)