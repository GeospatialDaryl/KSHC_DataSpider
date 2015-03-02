KSHC_DataSpider

Daryl Van Dyke - USFWS Klamath Strategic Habitat Conservation GIS Analyst
daryl_van_dyke@fws.gov

		"On two occasions I have been asked, 'Pray, Mr.
		Babbage, if you put into the machine wrong figures, 
		will the right answers come out?' I am not able 
		rightly to apprehend the kind of confusion of ideas 
		that could provoke such a question."
			-Charles Babbage, 
				on the difference engine


This repo contains the v1.0.1 python script SHC_DataSpider - a GIS data
inventory tool develop for the United States Fish & Wildlife Service's 
Strategic Habitat Conservation program.  

<mea>  This program contains both the original and *_v2 functions; once deployed
in beta I chose to template and replace the function calls rather than expunge
them.  That, and the devotedly sequential style makes this an OK approach.  
There were 'reasons' why I approached it this way, at the time; I'll add that not 
all of them were due to my lack of depth of OO-mindset.  

The other decision to discuss is the 'one giant list' processing order.  There 
were good reasons for that decision, as well, and I think the overall structure
 of the program is 'acceptable'.  However, future versions will be class based 
 in 'in-line' operations on the OS.WALK iterator are expected. 
<\mea>

The best use of this program is to cut-n-paste useful chunks out.  I am currently 
(8/2014) working on an updated, multiprocessing version.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.