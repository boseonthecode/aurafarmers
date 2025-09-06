import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Subject Manager',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        brightness: Brightness.dark,
      ),
      home: const SubjectManagerPage(),
    );
  }
}

class SubjectManagerPage extends StatefulWidget {
  const SubjectManagerPage({super.key});

  @override
  State<SubjectManagerPage> createState() => _SubjectManagerPageState();
}

class _SubjectManagerPageState extends State<SubjectManagerPage> {
  final List<Map<String, dynamic>> _subjects = [
    {'name': 'Math 1', 'isChecked': false},
    {'name': 'Chem', 'isChecked': false},
    {'name': 'Phy', 'isChecked': false},
    {'name': 'CompSci', 'isChecked': false},
  ];

  final TextEditingController _newSubjectController = TextEditingController();

  @override
  void dispose() {
    _newSubjectController.dispose();
    super.dispose();
  }

  void _addSubject(String subjectName) {
    if (subjectName.trim().isNotEmpty) {
      setState(() {
        _subjects.add({
          'name': subjectName.trim(),
          'isChecked': false,
        });
      });
      _newSubjectController.clear();
      
      // Show success message
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Added "$subjectName" successfully!'),
          backgroundColor: Colors.green,
          duration: const Duration(seconds: 2),
        ),
      );
    }
  }

  void _addSubjectDialog() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext dialogContext) {
        return AlertDialog(
          backgroundColor: Colors.grey[900],
          title: const Text(
            'Add New Subject',
            style: TextStyle(color: Colors.white),
          ),
          content: TextField(
            controller: _newSubjectController,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(
              hintText: "Enter subject name",
              hintStyle: TextStyle(color: Colors.grey),
              enabledBorder: UnderlineInputBorder(
                borderSide: BorderSide(color: Colors.white),
              ),
              focusedBorder: UnderlineInputBorder(
                borderSide: BorderSide(color: Colors.blue),
              ),
            ),
            autofocus: true,
            onSubmitted: (value) {
              _addSubject(value);
              Navigator.of(dialogContext).pop();
            },
          ),
          actions: [
            TextButton(
              onPressed: () {
                _newSubjectController.clear();
                Navigator.of(dialogContext).pop();
              },
              child: const Text(
                'Cancel',
                style: TextStyle(color: Colors.grey),
              ),
            ),
            ElevatedButton(
              onPressed: () {
                _addSubject(_newSubjectController.text);
                Navigator.of(dialogContext).pop();
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue,
              ),
              child: const Text(
                'Add',
                style: TextStyle(color: Colors.white),
              ),
            ),
          ],
        );
      },
    );
  }

  void _editSubject(int index, String newName) {
    if (newName.trim().isNotEmpty) {
      setState(() {
        _subjects[index]['name'] = newName.trim();
      });
    }
  }

  void _deleteSubject(int index) {
    final String subjectName = _subjects[index]['name'];
    setState(() {
      _subjects.removeAt(index);
    });
    
    // Show deletion message with undo option
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Deleted "$subjectName"'),
        backgroundColor: Colors.red,
        duration: const Duration(seconds: 3),
        action: SnackBarAction(
          label: 'Undo',
          textColor: Colors.white,
          onPressed: () {
            setState(() {
              _subjects.insert(index, {
                'name': subjectName,
                'isChecked': false,
              });
            });
          },
        ),
      ),
    );
  }

  void _editSubjectDialog(int index) {
    final TextEditingController editController =
        TextEditingController(text: _subjects[index]['name']);

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext dialogContext) {
        return AlertDialog(
          backgroundColor: Colors.grey[900],
          title: const Text(
            'Edit Subject',
            style: TextStyle(color: Colors.white),
          ),
          content: TextField(
            controller: editController,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(
              hintText: "Enter new name",
              hintStyle: TextStyle(color: Colors.grey),
              enabledBorder: UnderlineInputBorder(
                borderSide: BorderSide(color: Colors.white),
              ),
              focusedBorder: UnderlineInputBorder(
                borderSide: BorderSide(color: Colors.blue),
              ),
            ),
            autofocus: true,
            onSubmitted: (value) {
              _editSubject(index, value);
              Navigator.of(dialogContext).pop();
            },
          ),
          actions: [
            TextButton(
              onPressed: () {
                // Show confirmation dialog for deletion
                showDialog(
                  context: dialogContext,
                  builder: (BuildContext confirmContext) {
                    return AlertDialog(
                      backgroundColor: Colors.grey[900],
                      title: const Text(
                        'Delete Subject',
                        style: TextStyle(color: Colors.white),
                      ),
                      content: Text(
                        'Are you sure you want to delete "${_subjects[index]['name']}"?',
                        style: const TextStyle(color: Colors.white),
                      ),
                      actions: [
                        TextButton(
                          onPressed: () => Navigator.of(confirmContext).pop(),
                          child: const Text(
                            'Cancel',
                            style: TextStyle(color: Colors.grey),
                          ),
                        ),
                        ElevatedButton(
                          onPressed: () {
                            Navigator.of(confirmContext).pop();
                            Navigator.of(dialogContext).pop();
                            _deleteSubject(index);
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.red,
                          ),
                          child: const Text(
                            'Delete',
                            style: TextStyle(color: Colors.white),
                          ),
                        ),
                      ],
                    );
                  },
                );
              },
              child: const Text(
                'Delete',
                style: TextStyle(color: Colors.red),
              ),
            ),
            TextButton(
              onPressed: () {
                editController.dispose();
                Navigator.of(dialogContext).pop();
              },
              child: const Text(
                'Cancel',
                style: TextStyle(color: Colors.grey),
              ),
            ),
            ElevatedButton(
              onPressed: () {
                _editSubject(index, editController.text);
                editController.dispose();
                Navigator.of(dialogContext).pop();
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue,
              ),
              child: const Text(
                'Save',
                style: TextStyle(color: Colors.white),
              ),
            ),
          ],
        );
      },
    );
  }

  Future<void> _pickImage() async {
    try {
      final ImagePicker picker = ImagePicker();
      final XFile? photo = await picker.pickImage(
        source: ImageSource.camera,
        maxWidth: 1800,
        maxHeight: 1800,
        imageQuality: 85,
      );
      
      if (photo != null) {
        print('Image captured at: ${photo.path}');
        
        // Show success message
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Image captured successfully!'),
            backgroundColor: Colors.green,
            duration: Duration(seconds: 2),
          ),
        );
      }
    } catch (e) {
      print('Error picking image: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Failed to capture image. Please try again.'),
          backgroundColor: Colors.red,
          duration: Duration(seconds: 2),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: const Text('Subject Manager'),
        backgroundColor: Colors.grey[900],
        elevation: 0,
      ),
      body: LayoutBuilder(
        builder: (context, constraints) {
          if (constraints.maxWidth > 800) {
            // Desktop/Web layout
            return Row(
              children: [
                // Left side: Add Image
                Expanded(
                  child: _buildImageSection(),
                ),
                // Right side: Subjects list
                Expanded(
                  child: _buildSubjectsSection(),
                ),
              ],
            );
          } else {
            // Mobile layout
            return Column(
              children: [
                SizedBox(
                  height: 200,
                  child: _buildImageSection(),
                ),
                Expanded(
                  child: _buildSubjectsSection(),
                ),
              ],
            );
          }
        },
      ),
    );
  }

  Widget _buildImageSection() {
    return Container(
      padding: const EdgeInsets.all(20.0),
      child: GestureDetector(
        onTap: _pickImage,
        child: Container(
          decoration: BoxDecoration(
            border: Border.all(color: Colors.white, width: 2),
            borderRadius: BorderRadius.circular(20.0),
            color: Colors.grey[900]?.withOpacity(0.3),
          ),
          child: const Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.camera_alt,
                size: 50.0,
                color: Colors.white,
              ),
              SizedBox(height: 10),
              Text(
                'Add Image / Documents',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                ),
                textAlign: TextAlign.center,
              ),
              SizedBox(height: 5),
              Text(
                'Tap to capture',
                style: TextStyle(
                  color: Colors.grey,
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSubjectsSection() {
    return Container(
      padding: const EdgeInsets.all(20.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Subjects',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              IconButton(
                onPressed: _addSubjectDialog,
                icon: const Icon(
                  Icons.add_circle,
                  color: Colors.blue,
                  size: 35,
                ),
                tooltip: 'Add new subject',
              ),
            ],
          ),
          const SizedBox(height: 20),
          Expanded(
            child: _subjects.isEmpty
                ? const Center(
                    child: Text(
                      'No subjects added yet.\nTap + to add your first subject!',
                      style: TextStyle(
                        color: Colors.grey,
                        fontSize: 16,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  )
                : ListView.builder(
                    itemCount: _subjects.length,
                    itemBuilder: (context, index) {
                      final subject = _subjects[index];
                      return Card(
                        color: Colors.grey[900],
                        margin: const EdgeInsets.symmetric(vertical: 4),
                        child: CheckboxListTile(
                          title: Text(
                            subject['name'],
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 16,
                            ),
                          ),
                          value: subject['isChecked'],
                          onChanged: (bool? value) {
                            setState(() {
                              _subjects[index]['isChecked'] = value ?? false;
                            });
                          },
                          secondary: IconButton(
                            icon: const Icon(
                              Icons.edit,
                              color: Colors.blue,
                            ),
                            onPressed: () => _editSubjectDialog(index),
                            tooltip: 'Edit subject',
                          ),
                          activeColor: Colors.blue,
                          checkColor: Colors.white,
                        ),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }
}