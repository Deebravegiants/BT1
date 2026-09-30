# [M] Lack of Network Proxy Detection

## Summary
Severity: Medium
Contest weight: 0.5605
Dataset id: 12203
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The applications on iOS or Android platforms do not use plain-text communication and all traffic is encrypted by default via HTTPS. Such encryption needs to be enforced to effectively defeat man-in-the-middle attacks. However, there are several network sniffer applications (e.g., Fiddler, Charles) that are able to sniff and capture the packet encrypted by HTTPS, or even modify the packet content (if with the access to the certificate on the mobile device). With that, it is important to reliably detect the presence of a network proxy and avoid it as much as possible in wallet-like applications. Our analysis shows that the detection of the presence of possible network proxies is currently missing.

## Recommendation
Currently, the Android version of the wallet allows the user-installed certificate. We highly recommend modifying it to throw an exception after the system certificate verification fails (line 222).
```solidity
@Override
public void checkServerTrusted(X509Certificate[] chain, String authType) throws CertificateException {
    try {
        defaultTrustManager.checkServerTrusted(chain, authType);
    } catch (CertificateException ce) {
        throw new CertificateException("error in validating certificate " + ce);
    }
}
```
The proxy detection under iOS platform is for reference only:
```solidity
(BOOL) isVPNOn {
    BOOL flag = NO;
    CFDictionaryRef dicRef = CFNetworkCopySystemProxySettings();
    const CFStringRef proxyCFstr = (const CFStringRef) CFDictionaryGetValue(dicRef, (const void*) kCFNetworkProxiesHTTPProxy);
    NSString *proxy = (__bridge NSString *) proxyCFstr;
    if (proxy != NULL) {
        flag = YES;
    }
    return flag;
}
```
