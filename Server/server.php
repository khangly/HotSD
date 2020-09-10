<?php

$mysqli = new mysqli('mysql', 'khangly', '91FEyhBOOrFIhzba3TVANijH', 'khangly');
//$cache = new Memcached('sd');

//if (!is_array($cache->getServerList())) {
//    $cache->addServer('localhost', 11211);
//	$cache->setOption(Memcached::OPT_COMPRESSION, false);
//}

// The connection attempt failed!
if ($mysqli->connect_errno) {
    echo "Sorry, this website is experiencing problems.";
    exit;
}

// Perform an SQL query
$sql = "SELECT ThreadID, URL, Item, Yes, No FROM Threads ORDER BY ThreadID DESC LIMIT 64";
if (!$result = $mysqli->query($sql)) {
    // Oh no! The query failed. 
    echo "Sorry, the website is experiencing problems.";
    exit;
}

$threads = $result->fetch_all(MYSQLI_ASSOC);
$thread_ids = array_column($threads, 'ThreadID');
echo var_dump($threads);
echo var_dump($thread_ids);
//$thread_pids = 

//// Now, let's fetch five random actors and output their names to a list.
//// We'll add less error handling here as you can do that on your own now
//$sql = "SELECT actor_id, first_name, last_name FROM actor ORDER BY rand() LIMIT 5";
//if (!$result = $mysqli->query($sql)) {
    //echo "Sorry, the website is experiencing problems.";
    //exit;
//}

//// Print our 5 random actors in a list, and link to each actor
//echo "<ul>\n";
//while ($actor = $result->fetch_assoc()) {
    //echo "<li><a href='" . $_SERVER['SCRIPT_FILENAME'] . "?aid=" . $actor['actor_id'] . "'>\n";
    //echo $actor['first_name'] . ' ' . $actor['last_name'];
    //echo "</a></li>\n";
//}
//echo "</ul>\n";

 //The script will automatically free the result and close the MySQL
 //connection when it exits, but let's just do it anyways
//$result->free();
//$mysqli->close();
?>
