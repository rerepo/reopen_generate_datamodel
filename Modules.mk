LOCAL_PATH := $(call my-dir)

###################### datamodel ######################
include $(CLEAR_VARS)

LOCAL_MODULE := datamodel


LOCAL_MODULE_CLASS := EXECUTABLES

intermediates := $(local-intermediates-dir)
GEN :=
GEN += $(intermediates)/oam/ftl_oam_convert.c
GEN += $(intermediates)/oam/ftl_oam_convert.h
GEN += $(intermediates)/oam/ftl_oam_id.h
GEN += $(intermediates)/oam/ftl_oam_init.c
GEN += $(intermediates)/oam/ftl_oam_init.h

#$(GEN): PRIVATE_INPUT_FILE :=
$(GEN): PRIVATE_PATH := $(LOCAL_PATH)
$(GEN): PRIVATE_INTERMEDIATES_DIR := $(intermediates)

$(GEN): PRIVATE_CUSTOM_TOOL = python3 $(PRIVATE_PATH)/BuildSourceFiles.py -f $< -t $(PRIVATE_PATH)/template -p $(PRIVATE_INTERMEDIATES_DIR)
$(GEN): $(LOCAL_PATH)/Sercomm_STANDALONE_TDD_B_DataModel_RAW.xml
	$(transform-generated-source)
LOCAL_GENERATED_SOURCES += $(GEN)

LOCAL_SRC_FILES :=
LOCAL_SRC_FILES += main.c

LOCAL_C_INCLUDES += $(LOCAL_PATH)
LOCAL_C_INCLUDES += $(intermediates)

include $(BUILD_EXECUTABLE)

