# [C] YoutubeDLSharp allows command injection on windows system due to non sanitized arguments

## Summary
Severity: Critical
Advisory: GHSA-2jh5-g5ch-43q5
CVE: CVE-2025-43858
CWE: CWE-77, CWE-78
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2025-04-23
Source: https://github.com/advisories/GHSA-2jh5-g5ch-43q5
Type: github-advisory

## Affected
- NuGet: `YoutubeDLSharp` — affected >=1.0.0-beta4 <1.1.2

## Details
## Summary
This vulnerability only apply when running on a Windows OS.
An unsafe conversion of arguments allows the injection of a malicous commands when starting `yt-dlp` from a commands prompt.

> [!CAUTION]
> **NOTE THAT DEPENDING ON THE CONTEXT AND WHERE THE LIBRARY IS USED, THIS MAY HAVE MORE SEVERE CONSEQUENCES. FOR EXAMPLE, A USER USING THE LIBRARY LOCALLY IS A LOT LESS VULNERABLE THAN AN ASP.NET APPLICATION ACCEPTING INPUTS FROM A NETWORK/INTERNET.**

## Details

The vulnerability have been implemented in a commit (https://github.com/Bluegrams/YoutubeDLSharp/commit/fdf3256da18d0e2da4a2f33ad4a1b72ff8273a50) 3 year ago to fix a issue with unicode characters on Windows.  ( In the latest version at the time of writing this, the code seems to have moved here : https://github.com/Bluegrams/YoutubeDLSharp/blob/b2f7968a2ef06a9c7b2c212785cfeac0b187b6d8/YoutubeDLSharp/YoutubeDLProcess.cs#L87 )
In this commit, a new way of starting yt-dlp was implemented, method that was defined as the default behaviour.  

When the internal method [`ConvertToArgs`](https://github.com/Bluegrams/YoutubeDLSharp/commit/fdf3256da18d0e2da4a2f33ad4a1b72ff8273a50#diff-8ec44b4ade6ce6ed38ebf7e765dc86c426984a18304cd1cd320bf92500133c88R64) get called, the application will test multiples conditions to decide on how the yt-dlp application should be started. The condition we are interesed in, as well a the default one on Windows, is at [line 99](https://github.com/Bluegrams/YoutubeDLSharp/commit/fdf3256da18d0e2da4a2f33ad4a1b72ff8273a50#diff-8ec44b4ade6ce6ed38ebf7e765dc86c426984a18304cd1cd320bf92500133c88R99) . Inside the `if` statement, we can see that insead of directly calling the `yt-dlp` binary, a command prompt is opened to run `yt-dlp`.  

**The problem arises when you realize that both arguments in the `ConvertToArgs` method may be provided by an untrusted client.** Since the documentation of YoutubeDLSharp does not warn developers about this behavior, they might assume that the library handles this safely by ensuring that the arguments are secure to run inside a command prompt. Instead, the two potentially malicious arguments are directly appended to the command string without any sanitization (see line [104](https://github.com/Bluegrams/YoutubeDLSharp/commit/fdf3256da18d0e2da4a2f33ad4a1b72ff8273a50#diff-8ec44b4ade6ce6ed38ebf7e765dc86c426984a18304cd1cd320bf92500133c88R104) and [107](https://github.com/Bluegrams/YoutubeDLSharp/commit/fdf3256da18d0e2da4a2f33ad4a1b72ff8273a50#diff-8ec44b4ade6ce6ed38ebf7e765dc86c426984a18304cd1cd320bf92500133c88R107)).



## PoC
For this example, I'm going to use the version `1.1.1` and a method inside [YoutubeDL.cs](https://github.com/Bluegrams/YoutubeDLSharp/blob/b2f7968a2ef06a9c7b2c212785cfeac0b187b6d8/YoutubeDLSharp/YoutubeDL.cs). Assuming you are running on a Windows OS, this method will by default use a CMD to open yt-dlp.

```c#
using YoutubeDLSharp;

public async Task<RunResult<VideoData>> GetMediaInformation()
{
        YoutubeDL youtubeDl = new YoutubeDL();
	// Fetch media information using a badly crafted "url" (escaped)
	return await youtubeDl.RunVideoDataFetch("https://example.com/\" & start calc.exe");
}
```
At the call of `GetMediaInformation`, the method `RunVideoDataFetch` will be called, internally this method will call the vulnerable method [`ConvertToArgs`] resulting in the following string: 
```
/C chcp 65001 >nul 2>&1 && "yt-dlp.exe"  --external-downloader "m3u8:native" --external-downloader-args "ffmpeg:-nostats -loglevel 0" -o "C:\Users\<hidden>\Documents\GitHub\<hidden>\<hidden>\bin\Release\net8.0\%(title)s [%(id)s]_%(epoch)s.%(ext)s" --force-overwrites --no-part -i --ignore-config --ffmpeg-location "ffmpeg.exe" --exec "echo outfile: {}" -- "https://example.com/" & start calc.exe"
```
>[!NOTE]
> Some text have been replaced by `<hidden>` inside the command.

The important part here is at the end of the command, we can see `"https://example.com/" & start calc.exe"`, if we compare it with our  
malicious URL `https://example.com/" & start calc.exe`, we can see that the method added quotes at the start and the end of the string. However, our additional quote in the URL followed by the `&` character made it so the CMD interprets what follows the `&` as a new command, thus executing `yt-dlp` **AND** the *very* dangerous `start calc.exe` 😊.

Here is a screenshot of the processes using another malicious url `https://example.com/" & start msinfo32`
![showcase](https://github.com/user-attachments/assets/d6f5513c-a69b-4cdd-9820-3f4d71b5c457)

## Impact
Every users running a effected version on a Windows OS with the [`UseWindowsEncodingWorkaround`](https://github.com/Bluegrams/YoutubeDLSharp/commit/fdf3256da18d0e2da4a2f33ad4a1b72ff8273a50#diff-8ec44b4ade6ce6ed38ebf7e765dc86c426984a18304cd1cd320bf92500133c88R44) value defined to true (default behaviour). If you are using build-in methods form the [YoutubeDL.cs](https://github.com/Bluegrams/YoutubeDLSharp/blob/b2f7968a2ef06a9c7b2c212785cfeac0b187b6d8/YoutubeDLSharp/YoutubeDL.cs) file, the value is `true` by default and **you cannot disable it from theses methods**.

## Patch

Upgrade to **v.1.1.2 or higher** of YoutubeDLSharp. The `UseWindowsEncodingWorkaround` property has been removed entirely in v.1.1.2.

## Workaround
(only for v1.1.1 or lower, please upgrade to the latest version)

### Using `YoutubeDLProcess`
If you are using a `YoutubeDLProcess` object directly to communicate with yt-dlp, you can disable `UseWindowsEncodingWorkaround` to mitigate the vulnerability. Doing so will execute the yt-dlp binary directly. However, you will lose support for Unicode characters.
**Example:**
```c#
YoutubeDLProcess youtubeDLProc = new YoutubeDLProcess()
{
       UseWindowsEncodingWorkaround = false
};
```

### Sanitizing url
If you want to keep support for Unicode characters or are using methods from the [YoutubeDL.cs](https://github.com/Bluegrams/YoutubeDLSharp/blob/b2f7968a2ef06a9c7b2c212785cfeac0b187b6d8/YoutubeDLSharp/YoutubeDL.cs) file, you would need to manually sanitize your inputs until a version with a fix is released. For URL sanitization, I managed to prevent the exploitation of the PoC by creating this method. However, I can't guarantee it would work in every case.
```c#
		public static string? SanitizeUrl(string url)
		{
			// Parse the URL using Uri
			if (Uri.TryCreate(url, UriKind.Absolute, out Uri? urlUri))
			{
				// According to the microsoft docs getting the absolute url append
				// all of the others fields, theses fields get URI escaped when you GET them
				// (https://learn.microsoft.com/en-us/dotnet/api/system.uri.query?view=net-8.0#remarks) 
				return urlUri.AbsoluteUri;
			}
			// Invalid url format
			return null;
		}
```
This works because Uri properties have special characters like spaces and `"` escaped into percent numbers like `%20`, thus turning our malicous url into `https://example.com/%22%20&%20start%20calc.exe`.
**Note, however, that if you modify the options with which yt-dlp is run, you need to ensure every option is also sanitized (assuming they are taken from a untrusted user input). This method won't work as these options are not URLs.**

## References
- https://github.com/Bluegrams/YoutubeDLSharp/security/advisories/GHSA-2jh5-g5ch-43q5
- https://nvd.nist.gov/vuln/detail/CVE-2025-43858
- https://github.com/Bluegrams/YoutubeDLSharp/commit/b6051372bd5af30f95f73de47d9bc71c3a07de0f
- https://github.com/Bluegrams/YoutubeDLSharp/commit/fdf3256da18d0e2da4a2f33ad4a1b72ff8273a50
- https://github.com/Bluegrams/YoutubeDLSharp
