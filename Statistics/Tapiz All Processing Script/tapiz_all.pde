import java.util.*;
import java.io.*;
import processing.pdf.*;

String dataset = "/Volumes/NO NAME/Skeens/Statistics/Timestamp_Action_Stats/timestamp_action_sorted.csv";
String font_path = "/Users/raquelalvarez/Downloads/KauriKnits/kauri_knits.ttf";
String font_path_sans = "/Users/raquelalvarez/Downloads/KauriKnitsSans/kauri_knits_sans_borders.ttf";
String results = "/Users/raquelalvarez/Desktop/tapiz_all_no_grid.pdf";
String dict_file = "/Volumes/NO NAME/Skeens/Statistics/Timestamp_Action_Stats/dictionary.csv";

int num_of_cats = 61;
int num_of_actions = 175572;
int max_line = 370;
int max_y = 475; // 175572 / 370
int font_size = 11;
int margin = 18; // 5 mm

PFont knit_font;

List<String> pattern = new ArrayList();
HashMap<String, String> dictionary = new HashMap<String, String>();

List<String> actions;



void printLegend() {
  for (int i = 0; i < actions.size(); i++) {
    String s = String.valueOf(char('a' + i));
    println(actions.get(i) + " - " + s);
  }
}


String getLetter(String s) {
  int idx = actions.indexOf(s);
  String l = String.valueOf(char('a' + idx));
  return l;
}

void setup() {
  
  //int x_size = ((num_of_actions/16) * font_size) + (2 * font_size);
  //int y_size = (16 * font_size) + (2 * font_size);
  
 // printLegend();
  // 370 x 475
  // 370 * 11 = 4070
  // 475 * 11 = 5225
  // 4070 + (18*2) = 4106
  // 5225 + (18*2) = 5261
  // 5261 + 18 = 5279
  // 5279 + (20*11) + 18 = 5517
  size(4106, 5517, PDF, results);

  
  try {
    Scanner scanner = new Scanner(new File(dataset));
    Scanner scanner_dict = new Scanner(new File(dict_file));
    
    for (int i = 0; i < num_of_cats; i++) {
      String[] cat_letter = scanner_dict.nextLine().split(",");
      dictionary.put(cat_letter[0],cat_letter[1]);
      println(dictionary.get(cat_letter[0]));
    }
    scanner_dict.close();
    
    for (int i = 0; i < num_of_actions; i++) {
      String[] line = scanner.nextLine().split(",");
      if ((dictionary.get(line[1])) == null) {
        println(line[1]);
      }
      pattern.add(dictionary.get(line[1]));
    }
    println("Size of pattern: " + pattern.size());
    scanner.close();
  }
  catch(FileNotFoundException e) {
    println("Error could not open file.");
    println(e);
    exit();
  }
  
  knit_font = createFont(font_path_sans, font_size);
}


void draw() {
  
  int curr_line = 0;
  
  int h = font_size;
  int w = font_size;
  
  int curr_x = margin;
  int curr_y = margin + font_size;
  
  background(255);
  fill(0);
  
  // Legend
  /*
  int pos_y = margin + (font_size * num_of_actions) + margin;
  int pos_x = margin;
  int max_items = 3;
  int items = 0;
  for (String k: dictionary.keySet()) {
    String l = k + " - " + dictionary.get(k);
    text(l, pos_x, pos_y);
    items++;
    pos_x += (font_size * l.length()) + 2;
    if (items == 3) {
      pos_x = margin;
      pos_y += font_size;
      items = 0;
    }
  }
  */
  
  textMode(SHAPE);
  textFont(knit_font, font_size);
  
  println("Printing " + pattern.size() + " patterns.");
  
  boolean vertical_lines_done = false;
  
  stroke(#336DBC);
  //line(margin, margin, margin + (max_line*font_size), margin);
  //line(margin, curr_y, margin + (max_line*font_size), curr_y);
  //line(margin, margin, margin, margin + (max_y * font_size));
  for(int i = 0; i < num_of_actions; i++) {
     //println(pattern.get(i));
     fill(0);
     text(pattern.get(i), curr_x, curr_y);
     curr_line++;
     curr_x += w;
     if (curr_line == max_line) {
       vertical_lines_done = true;
       curr_x = margin;    // reset x to 12
       curr_y += h;           // move y down by 12
       curr_line = 0;
       stroke(#336DBC);
       //line(margin, curr_y, max_line*font_size, curr_y);
     }
     if (vertical_lines_done == false) {
       stroke(#336DBC);
       //line(curr_x, margin, curr_x, margin + (max_y * font_size));
     }
  }

  fill(#336DBC);
  //line(margin, curr_y, max_line*font_size, curr_y);
  println("Done!");
  
  noLoop(); 

  exit();
}
