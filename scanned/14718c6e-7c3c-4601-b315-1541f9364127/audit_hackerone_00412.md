# [C] Unchecked weapon id in WeaponList message parser on client leads to RCE

## Summary
Severity: Critical (CVSS 9.8)
Program: Valve
Weakness: Array Index Underflow
Reporter: nyancat0131
State: resolved
Disclosed: 2019-09-17T17:34:14.845Z
Source: https://hackerone.com/reports/513154

## Details
Let's look at WeaponList message parser code in the HLSDK:
``` cpp
int CHudAmmo::MsgFunc_WeaponList(const char *pszName, int iSize, void *pbuf )
{
	BEGIN_READ( pbuf, iSize );
	
	WEAPON Weapon;

	strcpy( Weapon.szName, READ_STRING() );
	Weapon.iAmmoType = (int)READ_CHAR();	
	
	Weapon.iMax1 = READ_BYTE();
	if (Weapon.iMax1 == 255)
		Weapon.iMax1 = -1;

	Weapon.iAmmo2Type = READ_CHAR();
	Weapon.iMax2 = READ_BYTE();
	if (Weapon.iMax2 == 255)
		Weapon.iMax2 = -1;

	Weapon.iSlot = READ_CHAR();
	Weapon.iSlotPos = READ_CHAR();
	Weapon.iId = READ_CHAR();
	Weapon.iFlags = READ_BYTE();
	Weapon.iClip = 0;

	gWR.AddWeapon( &Weapon );

	return 1;
}
```

And `WeaponResource::AddWeapon`:

``` cpp
void AddWeapon( WEAPON *wp ) 
{ 
		rgWeapons[ wp->iId ] = *wp;	
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/513154_
