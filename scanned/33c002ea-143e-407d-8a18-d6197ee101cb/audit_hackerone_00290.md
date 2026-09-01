# [M] NULL Pointer Dereference while unserialize php object

## Summary
Severity: Medium
Program: Internet Bug Bounty
Weakness: NULL Pointer Dereference
Reporter: hoangnguyen
State: resolved
Disclosed: 2019-11-12T09:19:52.381Z
CVE: CVE-2016-10162
Source: https://hackerone.com/reports/195688

## Details
Because no checking result of object_init_ex so that if user passing implement class, abstract class the result of this is FALSE and args is NULL, so that lead program crash
```	if (UNEXPECTED(class_type->ce_flags & (ZEND_ACC_INTERFACE|ZEND_ACC_TRAIT|ZEND_ACC_IMPLICIT_ABSTRACT_CLASS|ZEND_ACC_EXPLICIT_ABSTRACT_CLASS))) {
		if (class_type->ce_flags & ZEND_ACC_INTERFACE) {
			zend_throw_error(NULL, "Cannot instantiate interface %s", ZSTR_VAL(class_type->name));
		} else if (class_type->ce_flags & ZEND_ACC_TRAIT) {
			zend_throw_error(NULL, "Cannot instantiate trait %s", ZSTR_VAL(class_type->name));
		} else {
			zend_throw_error(NULL, "Cannot instantiate abstract class %s", ZSTR_VAL(class_type->name));
		}
		ZVAL_NULL(arg);
		Z_OBJ_P(arg) = NULL;
		return FAILURE;
	}

	if (UNEXPECTED(!(class_type->ce_flags & ZEND_ACC_CONSTANTS_UPDATED))) {
		if (UNEXPECTED(zend_update_class_constants(class_type) != SUCCESS)) {
			ZVAL_NULL(arg);
			Z_OBJ_P(arg) = NULL;
			return FAILURE;
		}
	}

	if (class_type->create_object == NULL) {
		ZVAL_OBJ(arg, zend_objects_new(class_type));
		if (properties) {
			object_properties_init_ex(Z_OBJ_P(arg), properties);
		} else {
			object_properties_init(Z_OBJ_P(arg), class_type);
		}
	} else {
		ZVAL_OBJ(arg, class_type->create_object(class_type));
	}
	return SUCCESS;
```
```
object_init_ex(&obj, pce);

							/* Merge current hashtable with object's default properties */
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/195688_
