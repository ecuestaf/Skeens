import java.io.File;
import java.io.FileNotFoundException;
import java.util.Scanner;

// ========================================
//   SETTINGS
// ========================================
// Colors
int background_color = #414346;
int line_color = #D6D7D8;
int line_transparency = 200;   // 200/255 = 78% opacity
int friend_sphere_color = #56A1FA;
int friend_sphere_transparency = 190;
int elisa_sphere_color = 255;
int elisa_sphere_transparency = 255;

// Thickness
float line_thickness = 0.75;

// Positioning
int space_between_lines = 50;

// Image Settings
String image_path = "/Users/raquelalvarez/Desktop/apollo_w_1440";
int number_of_images = 1;

// Dataset
String dataset_path = "/Users/raquelalvarez/Desktop/dataset_1440.csv";
String dataset_settings_path = "/Users/raquelalvarez/Desktop/settings_1440.csv";
// ========================================


// ========================================
//   Variables / Data Structures
// ========================================
int time = 0;
int message_size = 0;

int intervals = 0;
int left_margin = 0;  // margins have to be at least as big as the longest conversation
int right_margin = 0;

int x_axis = 0;
int y_axis = 0;
PGraphics pg;

int friends = 0;
int time_range = 0;
int max_word_count = 0;
int interaccion_counts[][];
// ========================================


// ========================================
//   SCRIPT
// ========================================
// Load Dataset
//  Reads the dataset file and extracts needed information
void load_dataset() {
  
  String[] line;
  
  try {
    
    // Open dataset CSV file
    //  * Expected File Structure (by line):
    //      number of friends (for the y axis)
    //      number of messages to display per friend (for the y axis)
    //      size of the longest message
    //      interaccion count for friend 1 (in the form: 1,-2,40,3, ...)
    //      interaccion count for friend 2
    //          . . .
    //      interaccion count for friend n (where n is the number of friends)
    Scanner scanner = new Scanner(new File(dataset_path));
    Scanner settings_scanner = new Scanner(new File(dataset_settings_path));
    
    // Read the file and save values in local variables
    intervals = Integer.parseInt(settings_scanner.nextLine());
    friends = Integer.parseInt(settings_scanner.nextLine());
    time_range = Integer.parseInt(settings_scanner.nextLine());
    max_word_count = Integer.parseInt(settings_scanner.nextLine());
    
    // DEBUG
    //  FOR TESTING ONE IMAGE ONLY
    //intervals = 180;
    //friends = 370;
    //time_range = 3308;
    //max_word_count = 532;
    
    // Set margins
    left_margin = max_word_count;
    right_margin = max_word_count;
    
    // Setup array of data
    interaccion_counts = new int[friends][time_range];
    for(int i = 0; i < friends; i++) {
      line = scanner.nextLine().split(",");
      for (int j = 0; j < time_range; j++) {
        interaccion_counts[i][j] = Integer.parseInt(line[j]);
      }
    }
    
    // Setup axis
    y_axis = (friends * space_between_lines) + (2*max_word_count);
    x_axis = left_margin + time_range/number_of_images + right_margin;
    
    // Close the dataset file
    scanner.close();
    settings_scanner.close();
    
  } catch (FileNotFoundException e) {
    println(" Error Opening Dataset/Settings File! Make sure the file exisits and the paths are correct on the script.");
    exit();
  }
  
  // Debug
  println("Dataset Settings:");
  println("  Friends: " + friends);
  println("  Time: " + time_range);
  println("  Longest message: " + max_word_count);
  println("  Intervals of: " + intervals);
  println("Image Settings:");
  println("  Size: " + x_axis + " by " + y_axis + "");
  // -----
  
}


void generate_image(int start_index, int end_index, int image_number) {
   
  // Setup the graphics object to be modifiabled
  pg.beginDraw();
  
  // Set the background of the image
  pg.background(background_color);
  
  // Draw the lines (one per friend)
  //println("Lines at..");
  for (int i = 1; i <= friends; i++) {
    pg.stroke(line_color);//, line_transparency);
    pg.strokeWeight(line_thickness);
    // Debug
    //println("(" + left_margin + "," + (i*space_between_lines) + ") -> (" + (x_axis-right_margin) + "," + (i*space_between_lines) + ")");
    // -----
    pg.line(left_margin, (left_margin + (i*space_between_lines)), x_axis-right_margin, (left_margin + (i*space_between_lines)));
    
  }
  println("\n");
  
  // Draw a sphere for each interaccion
  //    * Dataset Interpretation:
  //      - We use negative counts of words in a message to denote a message being sent by Elisa.
  //      - Positive counts correspond to the Friend.
  //      - This convention is used to reduce the amount of memory used to store the necessary details (count and sender).
  //    * Sphere Design:
  //      - The sphere's radius depends on the number of words on the message.
  //      - The sphere's color depends on who is sending the message.
  //println("Spheres at...");
  for (int i = 0; i < friends; i++) {
    
    for (int j = start_index; j < end_index; j++) {
      // color
      if (interaccion_counts[i][j] > 0) {
        pg.fill(friend_sphere_color, friend_sphere_transparency);
        message_size = interaccion_counts[i][j];
      } else if (interaccion_counts[i][j] < 0) {
        pg.fill(elisa_sphere_color, elisa_sphere_transparency);
        message_size = (-1) * interaccion_counts[i][j];
      } else {
        continue;
      }
      
      // Raquel - Red
      if (i == 41) {
        pg.fill(#ED2222);
      }
      
      // Marcos - Green
      if (i == 335) {
        pg.fill(#1BF524);
      }
      
      // stroke
      pg.noStroke();
      
      // draw
      pg.ellipse(left_margin+((j-start_index)), (left_margin + (i+1)*space_between_lines), message_size, message_size);
    }
  }
  
  // Save image to a file and print the time it takes
  println("\nSaving image...");
  time = millis();         // milliseconds the script has been executing for
  pg.save(image_path + "_" + image_number + ".png");
  time = millis() - time;  // milliseconds it took to save the image to a file
  println(time/1000 + " seconds... Done!");
  
  // Stop Drawing
  pg.endDraw();
}


// Setup
//  Creates graphic for image
void setup() {
  
  // Load dataset
  load_dataset();
  
  // Create a graphics object to be defined in draw()
  pg = createGraphics(x_axis, y_axis);
}

// Draw
//  Generates content in graphic and creates image
void draw() {
  
  // Generate graphics
  int start_index = 0;
  int end_index = time_range/number_of_images;
  for (int i = 0; i < number_of_images; i++) {
      println("Indices are... " + start_index + " to " + end_index);
      generate_image(start_index, end_index, i);
      start_index = end_index + 1;
      end_index = end_index + time_range/number_of_images;
  }

  println("\nImages generated. Good bye!");
  
  // Execute draw() only once
  noLoop();
}
