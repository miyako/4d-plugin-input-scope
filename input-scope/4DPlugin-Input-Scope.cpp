/* --------------------------------------------------------------------------------
 #
 #  4DPlugin-Input-Scope.cpp
 #	source generated by 4D Plugin Wizard
 #	Project : Input Scope
 #	author : miyako
 #	2019/07/24
 #  
 # --------------------------------------------------------------------------------*/

#include "4DPlugin-Input-Scope.h"

#pragma mark -

#if VERSIONWIN
#include "windows.h"
#include "inputscope.h"
#include <Imm.h>
#pragma comment(lib, "imm32.lib")
decltype(SetInputScope)*setInputScope = NULL;
HMODULE hMSCTF = NULL;
#endif

void PluginMain(PA_long32 selector, PA_PluginParameters params) {
    
	try
	{
        switch(selector)
        {
            case kInitPlugin:
            case kServerInitPlugin:
#if VERSIONWIN
                hMSCTF = LoadLibrary(TEXT("msctf.dll"));
                setInputScope = (decltype(SetInputScope)*)GetProcAddress(hMSCTF, "SetInputScope");
#endif
            break;
            
            case kDeinitPlugin:
            case kServerDeinitPlugin:
#if VERSIONWIN
            if(hMSCTF)
            {
                FreeLibrary(hMSCTF);
                hMSCTF = NULL;
            }
#endif
            break;
            
			// --- Input Scope
            
			case 1 :
				Set_input_scope(params);
				break;
                
            case 2 :
                Disable_input_method(params);
                break;

        }

	}
	catch(...)
	{

	}
}

#pragma mark -

void Set_input_scope(PA_PluginParameters params) {
    
    PA_long32 res = 0;
    
#if VERSIONWIN
    
    if(!PA_IsProcessDying()) {
        
        HWND hwnd = GetFocus();
        
        if(hwnd) {
        
            res = setInputScope(hwnd, (InputScope)PA_GetLongParameter(params, 1));
        }
    }
    
#endif
    PA_ReturnLong(params, res);
}

void Disable_input_method(PA_PluginParameters params)
{
    PA_long32 res = 0;
    
#if VERSIONWIN

    /*
          
     https://chromium.googlesource.com/chromium/src.git/+/8ced33be1ee63e589afff6f9229b36fe73cfd0f9/src/chrome/browser/ime_input.cc
     
     */
    
    if(!PA_IsProcessDying()) {
        PA_long32 event = PA_GetLongintVariable(PA_ExecuteCommandByID(COMMAND_FORM_EVENT, NULL, 0));
                    
            HWND hwnd = GetFocus();
            
            if(hwnd) {

				if (event != EVENT_ON_GETTING_FOCUS) {
					HIMC himc = ImmGetContext(hwnd);
					if (himc) {
						ImmNotifyIME(himc, NI_COMPOSITIONSTR, CPS_CANCEL, 0);
						ImmReleaseContext(hwnd, himc);
					}
				}

                res = ImmAssociateContextEx(hwnd, NULL, 0);
            }
        }
#endif
    PA_ReturnLong(params, res);
}