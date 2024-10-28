using System.IO;
using System.Runtime.Serialization.Formatters.Binary;

namespace XWS.Extension
{
    public class ByteConverter
    {
        /// <summary>
        /// Convert an object to a byte array
        /// </summary>
        /// <param name="obj">The object</param>
        /// <returns>The byte array</returns>
        public static byte[] ObjectToByteArray(object obj)
        {
            if (obj == null)
                return null;
            BinaryFormatter binForm = new BinaryFormatter();
            using (MemoryStream memStream = new MemoryStream())
            {
                binForm.Serialize(memStream, obj);
                return memStream.ToArray();
            }
        }
        /// <summary>
        /// Convert a byte array to an Object
        /// </summary>
        /// <param name="arrBytes">The byte array</param>
        /// <returns>The object</returns>
        public static object ByteArrayToObject(byte[] arrBytes)
        {
            MemoryStream memStream = new MemoryStream();
            BinaryFormatter binForm = new BinaryFormatter();
            memStream.Write(arrBytes, 0, arrBytes.Length);
            memStream.Seek(0, SeekOrigin.Begin);
            object obj = (object)binForm.Deserialize(memStream);

            return obj;
        }
    }
}