#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_LEDBackpack.h>
#include <MPU6050_light.h>

// I2C pins on RP2040
static const uint8_t SDA_PIN = 4;
static const uint8_t SCL_PIN = 5;

// HT16K33 matrix object
Adafruit_8x8matrix matrix;

// MPU object on Wire
MPU6050 mpu(Wire);

struct Vec3 {
  float x, y, z;
};

static Vec3 gravity_down_unit_from_accel(float ax, float ay, float az) {
  float mag = sqrtf(ax*ax + ay*ay + az*az);
  if (mag < 1e-6f) return {0, 0, 0};

  return { -ax / mag, -ay / mag, -az / mag };
}

struct Grain{
  int x, y;
};

const int GRAIN_COUNT = 25;
Grain grains[GRAIN_COUNT];

bool in_bounds(int x, int y){
  return x >= 0 && x < 8 && y >= 0 && y < 8;
}

void draw_grains(){
  matrix.clear();
  for(int i = 0; i < GRAIN_COUNT; i++){
    matrix.drawPixel(grains[i].x, grains[i].y, LED_ON);
  }

  matrix.writeDisplay();
}

void move_grains(float gx, float gy){
  bool occupied[8][8] = {false};

  for (int i = 0; i < GRAIN_COUNT; i++)
    occupied[grains[i].x][grains[i].y] = true;

  for (int step = 0; step < GRAIN_COUNT; step++) {
    int i = random(GRAIN_COUNT);

    int x = grains[i].x;
    int y = grains[i].y;

    int dx = (gx > 0.2) ? 1 : (gx < -0.2 ? -1 : 0);
    int dy = (gy > 0.2) ? 1 : (gy < -0.2 ? -1 : 0);

    int nx = x + dx;
    int ny = y + dy;

    if (in_bounds(nx, ny) && !occupied[nx][ny]) {
      occupied[x][y] = false;
      grains[i].x = nx;
      grains[i].y = ny;
      grains[i].y = ny;
      continue;
    }

    int side = random(2) ? 1 : -1;

    nx = x + dx + side;
    ny = y + dy;

    if (in_bounds(nx, ny) && !occupied[nx][ny]) {
      occupied[x][y] = false;
      grains[i].x = nx;
      grains[i].y = ny;
      occupied[nx][ny] = true;
    }
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  Wire.setSDA(SDA_PIN);
  Wire.setSCL(SCL_PIN);
  Wire.begin();
  Wire.setClock(400000);

  if (!matrix.begin(0x70)) {
    while (1) delay(10);
  }

  matrix.setBrightness(10);
  matrix.blinkRate(0);

  byte status = mpu.begin();
  if (status != 0) {
    Serial.println("MPU init failed (check power/wiring/AD0/NCS).");
    while (1) 
      delay(10);
  }

  int x = 0, y = 0;

  for(int i = 0; i < GRAIN_COUNT; i++){
    grains[i].x = x;
    grains[i].y = y;

    x++;

    if(x % 8 == 0){
      x = 0;
      y++;
    }
  }
}

void loop() {

  draw_grains();

   mpu.update();
   float ax = mpu.getAccX();
   float ay = mpu.getAccY();
   float az = mpu.getAccZ();

   Vec3 gdown = gravity_down_unit_from_accel(ax, ay, az);

   move_grains(gdown.y, -gdown.z);

  delay(50);
}