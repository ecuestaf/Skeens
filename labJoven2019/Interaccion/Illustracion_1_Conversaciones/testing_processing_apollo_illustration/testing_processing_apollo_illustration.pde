int x = 100;
int grow = 3;

int sum(int a, int b) {
 return a + b; 
}

void setup() {
  size(800,800);
  background(#414346);
  smooth();
}

void draw() {
  // Re-draw the background every time (the ball is "moving")
  background(#414346);
  
  // Draw a static circle
  fill(255);
  ellipse(400,400,10,10);
  
  // Lines
  //  - replace # of lines --> friends/connections
  for (int i = 0; i < height-30; i = i + 17) {
    stroke(#D6D7D8, 200);
    strokeWeight(0.25);
    line(30,30+i,width-30,30+i);
  }
  
  // Draw the ball
  //  - replace --> each ball is a conversation (height = width && height = # palabras)
  //  - Message:
  //      * Persona
  //      * Elisa | No Elisa
  //      * Reformatted UNIX Time -> 
  //      * Num of words
  int max_unix_time;
  int min_unix_time;
  // set size(max_unix_time - min_unix_time + 60, num_of_people + 60) in setup()
  int max_pixel_size_of_line = 800;
  // f(unix_time) = x_pixel

  fill(#56A1FA, 190);
  noStroke();
  ellipse(400,400,x,x);

  // Update ball's x coordinate
  x += grow;
  
  // Fix x if the ball is going out of bounds
  // (we account for the radius of the ellipse
  // being 50, so we stop when the side of the
  // ellipse is touching the wall, not the center)
  if ((x >= 200 - 50) || (x <= 10)) {
    grow = grow * (-1);
  }
  
  println(mouseX + "," + mouseY);
  
  noLoop();
}
