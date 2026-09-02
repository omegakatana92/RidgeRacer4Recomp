cmake_minimum_required(VERSION 3.20)
project(RidgeRacer4Recomp C CXX)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
set(PSXRECOMP_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/psxrecomp")
set(PSX_LAUNCHER OFF CACHE BOOL "" FORCE)
set(PSX_RECOMP_UI OFF CACHE BOOL "" FORCE)
include("${PSXRECOMP_ROOT}/runtime/runtime.cmake")
file(GLOB GAME_FULL CONFIGURE_DEPENDS
  "${CMAKE_CURRENT_SOURCE_DIR}/generated/*_full.c"
  "${CMAKE_CURRENT_SOURCE_DIR}/generated/*_full_*.c")
file(GLOB GAME_DISPATCH "${CMAKE_CURRENT_SOURCE_DIR}/generated/*_dispatch.c")
psxrecomp_add_runtime_target(psx-runtime
  GAME_GENERATED_FULL_C "${GAME_FULL}"
  GAME_GENERATED_DISPATCH_C "${GAME_DISPATCH}"
  BIOS_GENERATED_FULL_C "${CMAKE_CURRENT_SOURCE_DIR}/bios-generated/OpenBIOS_full.c"
  BIOS_GENERATED_DISPATCH_C "${CMAKE_CURRENT_SOURCE_DIR}/bios-generated/OpenBIOS_dispatch.c"
  WINDOW_TITLE "Ridge Racer 4 Recompiled"
  DEFAULT_GAME_CONFIG_PATH "game.toml"
)
target_compile_definitions(psx-runtime PRIVATE NOMINMAX WIN32_LEAN_AND_MEAN)
