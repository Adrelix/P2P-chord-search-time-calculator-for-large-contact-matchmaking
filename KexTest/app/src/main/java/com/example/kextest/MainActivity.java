package com.example.kextest;


import android.content.Context;
import android.os.Bundle;

import com.google.android.material.floatingactionbutton.FloatingActionButton;
import com.google.android.material.snackbar.Snackbar;

import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;

import android.util.Base64;
import android.view.View;

import android.view.Menu;
import android.view.MenuItem;
import android.widget.TextView;

import java.io.File;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Set;
import java.util.Random;

import java.lang.*;





public class MainActivity extends AppCompatActivity {

    private int numberOfTotalUsers = 100000000;
    private int numberOfUsers = 100000;
    private int numberOfContacts = 100;
    private String[] hashedRegUsers;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }

    public static void deleteCache(Context context) {
        try {
            File dir = context.getCacheDir();
            deleteDir(dir);
        } catch (Exception e) { e.printStackTrace();}
    }

    public static boolean deleteDir(File dir) {
        if (dir != null && dir.isDirectory()) {
            String[] children = dir.list();
            for (int i = 0; i < children.length; i++) {
                boolean success = deleteDir(new File(dir, children[i]));
                if (!success) {
                    return false;
                }
            }
            return dir.delete();
        } else if(dir!= null && dir.isFile()) {
            return dir.delete();
        } else {
            return false;
        }
    }

    public void start(View view) throws NoSuchAlgorithmException {
        int[] testContactsSizes = new int[]{50, 100, 250, 500, 750, 1000};
        int[] testPackageSizes = new int[]{10000, 25000, 50000, 100000, 250000, 500000}; //, 1000000, 1500000, 2000000

//        for(int contactSize : testContactsSizes){
//            for(int packageSize: testPackageSizes){
//                numberOfContacts = contactSize;
//                numberOfUsers =  packageSize;
//                startTest();
//            }
//        }

        for(int i = 0 ;i <10 ; i++){
            numberOfContacts = 1000;
            numberOfUsers =  100000;
            getApplicationContext().getCacheDir().delete();
            startTest();
        }

    }


    public void startTest() throws NoSuchAlgorithmException {


        hashedRegUsers = new String[numberOfUsers];
        for(int c = 0; c < numberOfUsers; c++){
            hashedRegUsers[c] = sha256(""+ c);
        }


        long startClientSetup = System.currentTimeMillis();
        Set<String> contactHashTable = setup();
        long endClientSetup = System.currentTimeMillis();


        long start = System.currentTimeMillis();
        List<String> results = findRegisteredUsers(contactHashTable);
        long end = System.currentTimeMillis();

        long clientResult = endClientSetup - startClientSetup;
        long nodeResult = end - start;

        TextView info = findViewById(R.id.info);
        TextView clientSetup = findViewById(R.id.clientAnswers);
        TextView nodeAnswer = findViewById(R.id.nodeAnswers);
        TextView answerList = findViewById(R.id.foundContacts);


        info.setText("Testing:\n"+ "Number of users: " + numberOfUsers + "\nNumber of contacts: " + numberOfContacts);
        clientSetup.setText(clientSetup.getText() + "\n"+ clientResult + "ms");
        nodeAnswer.setText(nodeAnswer.getText() + "\n"+ nodeResult + "ms");
        answerList.setText("Found: " + results.size() + " contacts");


//        StringBuilder strb = new StringBuilder();
//        for(String contact: results){
//            strb.append(contact + "\n");
//        }



    }

    private Set<String> setup() throws NoSuchAlgorithmException {
        Random rand = new Random();  
    
        String[] contactsHashed = new String[numberOfContacts];

        for(int c = 0; c < numberOfContacts; c++){
            contactsHashed[c] = sha256(""+ rand.nextInt(numberOfUsers));
        }

        Set<String> table = new HashSet<>(numberOfContacts);

        for(int i = 0; i < numberOfContacts; i++){
            table.add(contactsHashed[i]);
        }
        return table;
    }


    public List<String> findRegisteredUsers(Set<String> contacts) throws NoSuchAlgorithmException {
        int regUsers = numberOfUsers;
        List<String> results = new LinkedList<>();

        for(Integer i = 0; i < regUsers ; i++){
            if(contacts.contains(hashedRegUsers[i])){
                results.add(i.toString());
            }
        }
        return results;
    }

    public String sha256(String input) throws NoSuchAlgorithmException {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        md.update(input.getBytes());
        byte[] digest = md.digest();
        return Base64.encodeToString(digest, Base64.DEFAULT);
//        return DatatypeConverter.printHexBinary(digest).toUpperCase();
    }
}