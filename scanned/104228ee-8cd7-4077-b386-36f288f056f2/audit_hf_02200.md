# [M] Possible Privilege Escalation in Plug-in xuexiangjys

## Summary
Severity: Medium
Contest weight: 0.4495
Dataset id: 12204
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The implementation of QR code scanning imports the third-party plug-in com.github.xuexiangjys.XUtil:xutil-core v1.1.5, where the function com.xuexiang.xutil.common.ShellUtils.execCommand has unsafely invoked exec of Runtime. Moreover, the exec also tries to call the command su. Though we have not found the actual risk caused by this behavior, we strongly recommend not to use this plug-in. * execute shell commands * @param commands command array * @param isRoot whether need to run with root * @param isNeedResultMsg whether need result msg * @return <ul> * <li>if isNeedResultMsg is false, {@link CommandResult # successMsg} is null and {@link CommandResult #errorMsg} is null.</li> * <li>if {@link CommandResult #result} is -1, there maybe some exception.</li> * </ul>
```solidity
public static CommandResult execCommand(String[] commands, boolean isRoot, boolean isNeedResultMsg) {
    int result = 1;
    if (commands == null || commands.length == 0)
        return new CommandResult(result, null, null);
    Process process = null;
    BufferedReader successResult = null;
    BufferedReader errorResult = null;
    StringBuilder successMsg = null;
    StringBuilder errorMsg = null;
    DataOutputStream os = null;
    try {
        process = Runtime.getRuntime().exec(isRoot ? COMMAND_SU : COMMAND_SH);
        os = new DataOutputStream(process.getOutputStream());
        for (String command : commands) {
            if (command == null)
                continue;
            // donnot use os.writeBytes(commmand), avoid chinese charset error
            os.write(command.getBytes());
            os.writeBytes(COMMAND_LINE_END);
        }
        os.flush();
        os.writeBytes(COMMAND_EXIT);
        os.flush();
        result = process.waitFor();
    }
```

## Recommendation
Remove the plug-in com.github.xuexiangjys.XUtil:xutil-core v1.1.5, or revise the current version to get rid of any unsafe usage.
