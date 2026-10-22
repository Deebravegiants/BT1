# [M] Flawed System Security Validation

## Summary
Severity: Medium
Contest weight: 0.3886
Dataset id: 12207
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Once the mobile platform's underlying operating system has been rooted or somehow hooked, the adversary could easily obtain all the local information of device, e.g., the user's password. Moreover, it is also possible to retrieve the private key temporarily stored in the memory through known code injection techniques.

## Recommendation
We highly recommend for the wallet to validate whether there is a possibility that the user's device is rooted or hooked, and clearly inform the potential risk to the user. Public Suggested Detection Method There are many related items in Android, please refer to the link for details: https://github.com/hamada147/AndroidRootChecker/blob/master/RootChecker.java. In iOS, please refer to the following code snippet:
```solidity
+ (BOOL) isJailBreakingByPath {
    NSArray *jailbreak_tool_paths = @[@"/Applications/Cydia.app", @"/Library/MobileSubstrate/MobileSubstrate.dylib", @"/bin/bash", @"/usr/sbin/sshd", @"/etc/apt"];
    for (int i = 0; i < jailbreak_tool_paths.count; i++) {
        if ([[NSFileManager defaultManager] fileExistsAtPath:jailbreak_tool_paths[i]]) {
            NSLog(@"The device is jail broken by path: %@!", jailbreak_tool_paths[i]);
            return YES;
        }
    }
    return NO;
}
```
